############################
## The Monty Hall Problem ##
############################

monty_hall_sim <- function(num_samp, num_sim){
  # Simulate the probability of winning based on tracking the number of times
  # the contestant wins if they were to switch and the number of times the
  # contestant wins if they didn't switch
  winning.outcome.probs <- c()
  
  # Door Options
  doors <- c("1","2","3")
  
  for (i in 1:num_samp){ # Number of Samples to Run
    winning.outcomes <- c()
    for (j in 1:num_sim){ # Number of Simulations to Conduct in Each Sample
      # Randomly Assign Which Door The Car Is Behind
      car.door <- sample(doors, 1)
      
      # Contestant Randomly Chooses A Door
      contestant.door <- sample(doors, 1)
      
      # Determine The Winning Scenario
      # switch -> If The Contestant Would Have Won By Switching
      # no.switch -> If The Contestant Would Have Won By Not Switching
      outcome <- ifelse(car.door == contestant.door, "no.switch", "switch")
      winning.outcomes <- append(winning.outcomes, outcome)
    }
    winning.outcome.probs <- append(winning.outcome.probs, 
                                    (sum(winning.outcomes == "switch")/length(winning.outcomes)))
  }
  
  avg.prob <- mean(winning.outcome.probs)
  return(avg.prob)
}

# Example call to function
monty_hall_sim(1000, 1000)

##########################
## Backward Elimination ##
##########################

# Function to check if a package is installed
isInstalled <- function(package_name) package_name %in% rownames(installed.packages())

if (!isInstalled("car")) install.packages("car")

# Load the necessary package
library(car)

backward_elimination <- function(df, response) {
  i <- ncol(df) - 1
  while (i > 1) {
    # Generate the equation to regress the dependent variable on all the independent variables
    eq <- paste(response, "~.", sep = "")
    # Run multiple linear regression model with all the independent variables
    mlr <- lm(eq, data = df)
    # Generate a Type II Anova table with associated p-values
    mlr_anova <- Anova(mlr)
    # Access the p-values from the Anova table
    pvalues <- mlr_anova[, 4][1:(ncol(df) - 1)]
    if (max(pvalues) < 0.05 | i == 2) {
      break 
    } else {
      removeVar <- rownames(mlr_anova)[which(pvalues == max(pvalues))]
      # Remove the independent variable column that has the highest p-value
      # and run the complete mlr without that column
      df <- df[-which(colnames(df) == removeVar)]
    }
    i <- i - 1 }
  # Return the name(s) of the independent variable(s) to include in the model
  return(colnames(df[-which(colnames(df) == response)]))
}

# Read in the data
startups <- read.csv("~/Desktop/50-Startups.csv", header = TRUE)

# Example call to function
backward_elimination(startups, "Profit")
